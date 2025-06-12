"""
Tests para GitHub Integration.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations import GitHubIntegration


class TestGitHubIntegration(unittest.TestCase):
    """Test GitHub integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github = GitHubIntegration()
    
    @patch('subprocess.run')
    def test_verify_gh_cli_authenticated(self, mock_run):
        """Test gh CLI verification when authenticated."""
        mock_run.return_value = MagicMock(returncode=0)
        
        github = GitHubIntegration()
        self.assertIsNotNone(github)
    
    @patch('subprocess.run')
    def test_verify_gh_cli_not_authenticated(self, mock_run):
        """Test gh CLI verification when not authenticated."""
        mock_run.return_value = MagicMock(returncode=1)
        
        github = GitHubIntegration()
        self.assertIsNotNone(github)  # Should still create object
    
    @patch('subprocess.run')
    def test_create_branch(self, mock_run):
        """Test branch creation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.github.create_branch("feature/test-branch")
        self.assertTrue(result)
        
        # Verify git commands were called
        calls = mock_run.call_args_list
        self.assertEqual(len(calls), 2)  # fetch + checkout
    
    @patch('subprocess.run')
    def test_create_pr(self, mock_run):
        """Test PR creation."""
        # Mock git branch command
        branch_result = MagicMock()
        branch_result.stdout = "feature/test\n"
        branch_result.returncode = 0
        
        # Mock gh pr create command
        pr_result = MagicMock()
        pr_result.stdout = json.dumps({
            "number": 123,
            "url": "https://github.com/user/repo/pull/123",
            "title": "Test PR"
        })
        pr_result.returncode = 0
        
        mock_run.side_effect = [branch_result, MagicMock(returncode=0), pr_result]
        
        pr_data = self.github.create_pr(
            title="Test PR",
            body="Test description",
            labels=["test", "automated"]
        )
        
        self.assertIsNotNone(pr_data)
        self.assertEqual(pr_data['number'], 123)
        self.assertIn('github.com', pr_data['url'])
    
    @patch('subprocess.run')
    def test_create_issue(self, mock_run):
        """Test issue creation."""
        issue_result = MagicMock()
        issue_result.stdout = json.dumps({
            "number": 456,
            "url": "https://github.com/user/repo/issues/456",
            "title": "Test Issue"
        })
        issue_result.returncode = 0
        
        mock_run.return_value = issue_result
        
        issue_data = self.github.create_issue(
            title="Test Issue",
            body="Test description",
            labels=["bug"]
        )
        
        self.assertIsNotNone(issue_data)
        self.assertEqual(issue_data['number'], 456)
    
    @patch('subprocess.run')
    def test_list_prs(self, mock_run):
        """Test listing PRs."""
        list_result = MagicMock()
        list_result.stdout = json.dumps([
            {
                "number": 1,
                "title": "PR 1",
                "author": {"login": "user1"},
                "createdAt": "2024-01-01",
                "url": "https://github.com/user/repo/pull/1"
            }
        ])
        list_result.returncode = 0
        
        mock_run.return_value = list_result
        
        prs = self.github.list_prs()
        self.assertEqual(len(prs), 1)
        self.assertEqual(prs[0]['number'], 1)
    
    def test_create_pr_for_task(self):
        """Test creating PR from task result."""
        task_result = {
            'description': 'Implement new feature',
            'changes': ['Added feature X', 'Updated docs'],
            'notes': 'All tests passing'
        }
        
        with patch.object(self.github, 'create_pr') as mock_create:
            mock_create.return_value = {'number': 789, 'url': 'http://...'}
            
            result = self.github.create_pr_for_task(task_result, 'Alfred')
            
            mock_create.assert_called_once()
            args = mock_create.call_args[1]
            self.assertIn('Implement new feature', args['title'])
            self.assertIn('Alfred', args['body'])
            self.assertIn('automated', args['labels'])
    
    def test_create_issue_for_error(self):
        """Test creating issue from error."""
        error = {
            'message': 'Division by zero',
            'traceback': 'Traceback...',
            'agent': 'Robin',
            'timestamp': '2024-01-01 12:00'
        }
        
        with patch.object(self.github, 'create_issue') as mock_create:
            mock_create.return_value = {'number': 111, 'url': 'http://...'}
            
            result = self.github.create_issue_for_error(error, "During calculation")
            
            mock_create.assert_called_once()
            args = mock_create.call_args[0]
            self.assertIn('Division by zero', args[0])  # title
            self.assertIn('Robin', args[1])  # body
    
    @patch('subprocess.run')
    def test_merge_pr(self, mock_run):
        """Test merging a PR."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.github.merge_pr(123, method="squash")
        self.assertTrue(result)
        
        # Check command
        cmd = mock_run.call_args[0][0]
        self.assertIn('merge', cmd)
        self.assertIn('--squash', cmd)
        self.assertIn('123', cmd)
    
    def test_setup_github_actions(self):
        """Test GitHub Actions setup."""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('pathlib.Path.write_text') as mock_write:
                result = self.github.setup_github_actions()
                
                self.assertTrue(result)
                mock_mkdir.assert_called_once()
                mock_write.assert_called_once()
                
                # Check workflow content
                workflow_content = mock_write.call_args[0][0]
                self.assertIn('Batman CI', workflow_content)
                self.assertIn('pytest', workflow_content)


if __name__ == '__main__':
    unittest.main()