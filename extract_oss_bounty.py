#!/usr/bin/env python3
"""
从 bounty-targets-data 提取所有提供赏金且 scope 包含开源仓库 (GitHub/GitLab) 的项目
只输出规范化的仓库 URL
"""

import json
import re
from pathlib import Path

# 匹配 GitHub/GitLab/Bitbucket 仓库的正则 (捕获 org/repo 部分)
REPO_PATTERN = re.compile(
    r'(?:https?://)?(?:www\.)?(github\.com|gitlab\.com|bitbucket\.org)/([^\s,;#\)]+)',
    re.IGNORECASE
)

def normalize_repo_url(raw: str) -> list:
    """
    从原始字符串中提取并规范化仓库 URL
    返回规范化后的 URL 列表
    """
    results = []
    raw = raw.strip()
    
    # 尝试匹配完整 URL
    for match in REPO_PATTERN.finditer(raw):
        host = match.group(1).lower()
        path = match.group(2).rstrip('/')
        
        # 清理路径中的尾随字符
        path = re.sub(r'[,;#\)\]\}]+$', '', path)
        path = path.rstrip('/')
        
        # 跳过只有组织名没有仓库名的情况，除非是通配符
        if '/' not in path and not path.endswith('*'):
            # 这可能是组织级别的 scope，保留它
            url = f"https://{host}/{path}"
        else:
            url = f"https://{host}/{path}"
        
        results.append(url)
    
    # 如果没有匹配到完整 URL，尝试匹配 org/repo 格式 (如 nextcloud/server)
    if not results:
        simple_pattern = re.compile(r'^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_\-\.\*]+)$')
        match = simple_pattern.match(raw)
        if match:
            org, repo = match.groups()
            results.append(f"https://github.com/{org}/{repo}")
    
    return results


def extract_from_hackerone(data):
    """HackerOne 数据格式"""
    results = []
    for program in data:
        if not program.get('offers_bounties', False):
            continue
        
        program_name = program.get('name', 'Unknown')
        program_url = program.get('url', '')
        
        in_scope = program.get('targets', {}).get('in_scope', [])
        repos = []
        for target in in_scope:
            asset_id = target.get('asset_identifier', '')
            asset_type = target.get('asset_type', '')
            eligible = target.get('eligible_for_bounty', False)
            
            if eligible and (asset_type == 'SOURCE_CODE' or 'github' in asset_id.lower() or 'gitlab' in asset_id.lower()):
                normalized = normalize_repo_url(asset_id)
                repos.extend(normalized)
        
        if repos:
            results.append({
                'platform': 'HackerOne',
                'program': program_name,
                'program_url': program_url,
                'repos': list(set(repos))  # 去重
            })
    return results


def extract_from_bugcrowd(data):
    """Bugcrowd 数据格式"""
    results = []
    for program in data:
        max_payout = program.get('max_payout') or 0
        if not max_payout > 0:
            continue
        
        program_name = program.get('name', 'Unknown')
        program_url = program.get('url', '')
        
        in_scope = program.get('targets', {}).get('in_scope', [])
        repos = []
        for target in in_scope:
            target_url = target.get('target', '') or target.get('uri', '')
            
            if 'github' in target_url.lower() or 'gitlab' in target_url.lower():
                normalized = normalize_repo_url(target_url)
                repos.extend(normalized)
        
        if repos:
            results.append({
                'platform': 'Bugcrowd',
                'program': program_name,
                'program_url': program_url,
                'repos': list(set(repos))
            })
    return results


def extract_from_yeswehack(data):
    """YesWeHack 数据格式"""
    results = []
    for program in data:
        min_bounty = program.get('min_bounty') or 0
        max_bounty = program.get('max_bounty') or 0
        if not (min_bounty > 0 or max_bounty > 0):
            continue
        
        program_name = program.get('name', 'Unknown')
        program_id = program.get('id', '')
        program_url = f"https://yeswehack.com/programs/{program_id}" if program_id else ''
        
        in_scope = program.get('targets', {}).get('in_scope', [])
        repos = []
        for target in in_scope:
            target_url = target.get('target', '')
            
            if 'github' in target_url.lower() or 'gitlab' in target_url.lower():
                normalized = normalize_repo_url(target_url)
                repos.extend(normalized)
        
        if repos:
            results.append({
                'platform': 'YesWeHack',
                'program': program_name,
                'program_url': program_url,
                'repos': list(set(repos))
            })
    return results


def extract_from_intigriti(data):
    """Intigriti 数据格式"""
    results = []
    for program in data:
        min_bounty = program.get('min_bounty', {})
        max_bounty = program.get('max_bounty', {})
        has_bounty = (min_bounty.get('value', 0) > 0 if isinstance(min_bounty, dict) else (min_bounty or 0) > 0) or \
                     (max_bounty.get('value', 0) > 0 if isinstance(max_bounty, dict) else (max_bounty or 0) > 0)
        
        if not has_bounty:
            continue
        
        program_name = program.get('name', 'Unknown')
        program_url = program.get('url', '')
        
        in_scope = program.get('targets', {}).get('in_scope', [])
        repos = []
        for target in in_scope:
            target_url = target.get('endpoint', '') or target.get('target', '')
            
            if 'github' in target_url.lower() or 'gitlab' in target_url.lower():
                normalized = normalize_repo_url(target_url)
                repos.extend(normalized)
        
        if repos:
            results.append({
                'platform': 'Intigriti',
                'program': program_name,
                'program_url': program_url,
                'repos': list(set(repos))
            })
    return results


def extract_from_federacy(data):
    """Federacy 数据格式"""
    results = []
    for program in data:
        if not program.get('offers_bounty', False):
            continue
        
        program_name = program.get('name', 'Unknown')
        program_url = program.get('url', '')
        
        in_scope = program.get('targets', {}).get('in_scope', [])
        repos = []
        for target in in_scope:
            target_url = target.get('target', '') or target.get('identifier', '')
            
            if 'github' in target_url.lower() or 'gitlab' in target_url.lower():
                normalized = normalize_repo_url(target_url)
                repos.extend(normalized)
        
        if repos:
            results.append({
                'platform': 'Federacy',
                'program': program_name,
                'program_url': program_url,
                'repos': list(set(repos))
            })
    return results


def load_manual_additions():
    """加载手动补充的项目列表"""
    manual_file = Path(__file__).parent / 'manual_additions.txt'
    if not manual_file.exists():
        return set()
    
    repos = set()
    with open(manual_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # 支持完整 URL 或 org/repo 格式
                normalized = normalize_repo_url(line)
                if normalized:
                    repos.update(normalized)
                elif line:
                    repos.add(line)
    return repos


def main():
    data_dir = Path(__file__).parent / 'data'
    output_file = Path(__file__).parent / 'oss_bounty_targets.txt'
    
    platforms = {
        'hackerone_data.json': extract_from_hackerone,
        'bugcrowd_data.json': extract_from_bugcrowd,
        'yeswehack_data.json': extract_from_yeswehack,
        'intigriti_data.json': extract_from_intigriti,
        'federacy_data.json': extract_from_federacy,
    }
    
    all_results = []
    
    for filename, extractor in platforms.items():
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"[!] 跳过: {filename} 不存在")
            continue
        
        platform_name = filename.replace('_data.json', '').title()
        print(f"[*] 正在处理 {platform_name}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = extractor(data)
        all_results.extend(results)
        print(f"    找到 {len(results)} 个包含开源仓库的赏金项目")
    
    print(f"\n[+] 总计找到 {len(all_results)} 个项目")
    
    # 写入详细文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in all_results:
            f.write(f"\n# === {item['platform']} - {item['program']} ===\n")
            f.write(f"# Program URL: {item['program_url']}\n")
            for repo in sorted(item['repos']):
                f.write(f"{repo}\n")
    
    print(f"[+] 详细结果已保存到: {output_file}")
    
    # 输出去重后的仓库列表
    repos_only_file = Path(__file__).parent / 'oss_repos_only.txt'
    all_repos = set()
    for item in all_results:
        for repo in item['repos']:
            all_repos.add(repo)
    
    # 合并手动补充的项目
    manual_repos = load_manual_additions()
    if manual_repos:
        print(f"[*] 加载手动补充项目: {len(manual_repos)} 个")
        all_repos.update(manual_repos)
    
    with open(repos_only_file, 'w', encoding='utf-8') as f:
        for repo in sorted(all_repos):
            f.write(f"{repo}\n")
    
    print(f"[+] 去重仓库列表已保存到: {repos_only_file}")
    print(f"[+] 共 {len(all_repos)} 个唯一仓库 URL")


if __name__ == '__main__':
    main()
